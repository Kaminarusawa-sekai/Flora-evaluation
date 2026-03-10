"""LLM-based cluster refiner for handling scattered/atomic APIs."""

from typing import List, Dict, Any, Optional
from collections import defaultdict
import json
import os


class LLMClusterRefiner:
    """
    Use LLM to refine scattered APIs into meaningful clusters.

    Strategy:
    1. Identify scattered APIs (clusters with 1-3 APIs)
    2. Use LLM to analyze semantic relationships
    3. Either merge into existing clusters or create new semantic groups
    """

    def __init__(self,
                 min_cluster_size: int = 3,
                 llm_provider: str = "rule",
                 api_key: Optional[str] = None,
                 model: Optional[str] = None,
                 api_base: Optional[str] = None):
        """
        Initialize LLM cluster refiner.

        Args:
            min_cluster_size: Clusters smaller than this are considered scattered
            llm_provider: LLM provider to use:
                - "rule": Rule-based fallback (default, no LLM needed)
                - "openai": OpenAI API (gpt-4, gpt-3.5-turbo, etc.)
                - "qwen": Alibaba Qwen (qwen-turbo, qwen-plus, qwen-max)
                - "deepseek": DeepSeek API (deepseek-chat, deepseek-coder)
                - "zhipu": Zhipu AI (glm-4, glm-3-turbo)
                - "ollama": Local Ollama (llama2, qwen, etc.)
                - "openai-compatible": Any OpenAI-compatible API
            api_key: API key for the provider
            model: Model name (provider-specific, auto-selected if None)
            api_base: Custom API base URL (for openai-compatible or custom endpoints)
        """
        self.min_cluster_size = min_cluster_size
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key or self._get_default_api_key()
        self.model = model or self._get_default_model()
        self.api_base = api_base or self._get_default_api_base()

        # Validate configuration
        if self.llm_provider != "rule" and self.llm_provider != "ollama":
            if not self.api_key:
                raise ValueError(f"API key required for provider: {self.llm_provider}")

    def _get_default_api_key(self) -> Optional[str]:
        """Get default API key based on provider."""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
        }
        env_var = key_map.get(self.llm_provider)
        return os.getenv(env_var) if env_var else None

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        model_map = {
            "openai": "gpt-4",
            "qwen": "qwen-plus",
            "deepseek": "deepseek-chat",
            "zhipu": "glm-4",
            "ollama": "llama2",
            "openai-compatible": "gpt-3.5-turbo",
            "rule": "rule-based"
        }
        return model_map.get(self.llm_provider, "gpt-3.5-turbo")

    def _get_default_api_base(self) -> Optional[str]:
        """Get default API base URL based on provider."""
        base_map = {
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "ollama": "http://localhost:11434",
        }
        return base_map.get(self.llm_provider)

    def refine(self, clustered_apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine clusters by processing scattered APIs with LLM.

        Args:
            clustered_apis: List of APIs with cluster assignments

        Returns:
            Refined list of APIs with updated cluster assignments
        """
        # Step 1: Identify scattered and stable clusters
        cluster_groups = defaultdict(list)
        for api in clustered_apis:
            cluster_id = api.get('cluster', -1)
            cluster_groups[cluster_id].append(api)

        scattered_apis = []
        stable_clusters = []

        for cluster_id, apis in cluster_groups.items():
            if len(apis) < self.min_cluster_size:
                scattered_apis.extend(apis)
            else:
                stable_clusters.append({
                    'cluster_id': cluster_id,
                    'apis': apis,
                    'entity': apis[0].get('entity_anchor', 'unknown'),
                    'size': len(apis)
                })

        if not scattered_apis:
            print("No scattered APIs found. All clusters are stable.")
            return clustered_apis

        print(f"\nFound {len(scattered_apis)} scattered APIs in {len([c for c in cluster_groups.values() if len(c) < self.min_cluster_size])} small clusters")
        print(f"Stable clusters: {len(stable_clusters)}")

        # Step 2: Use LLM to analyze scattered APIs
        refined_scattered = self._llm_analyze_scattered(scattered_apis, stable_clusters)

        # Step 3: Merge results
        result = []

        # Add stable clusters
        for cluster in stable_clusters:
            result.extend(cluster['apis'])

        # Add refined scattered APIs
        result.extend(refined_scattered)

        return result

    def _llm_analyze_scattered(self,
                               scattered_apis: List[Dict[str, Any]],
                               stable_clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use LLM to analyze scattered APIs and assign them to clusters.
        """
        # Build context for LLM
        scattered_summary = self._build_api_summary(scattered_apis)
        stable_summary = self._build_cluster_summary(stable_clusters)

        prompt = self._build_analysis_prompt(scattered_summary, stable_summary)

        print("\n" + "="*80)
        print("Calling LLM for scattered API analysis...")
        print("="*80)

        # Call LLM
        llm_response = self._call_llm(prompt, scattered_apis)

        print("\nLLM Response received. Parsing...")

        # Parse LLM response and apply assignments
        assignments = self._parse_llm_response(llm_response, scattered_apis)

        # Apply assignments
        next_cluster_id = max([c['cluster_id'] for c in stable_clusters]) + 1 if stable_clusters else 0

        for i, api in enumerate(scattered_apis):
            if i in assignments:
                assignment = assignments[i]

                if assignment['action'] == 'merge':
                    # Merge into existing cluster
                    api['cluster'] = assignment.get('target_cluster', next_cluster_id)
                    api['cluster_type'] = 'llm_merged'
                    api['llm_reason'] = assignment.get('reason', '')
                    print(f"  [{i}] MERGE into cluster {api['cluster']}: {assignment.get('reason', '')}")
                elif assignment['action'] == 'group':
                    # Create new group
                    cluster_id = assignment.get('new_cluster_id', next_cluster_id)
                    api['cluster'] = cluster_id
                    api['cluster_type'] = 'llm_grouped'
                    api['llm_reason'] = assignment.get('reason', '')
                    print(f"  [{i}] GROUP into new cluster {cluster_id}: {assignment.get('reason', '')}")
                else:
                    # Keep as atomic
                    api['cluster_type'] = 'llm_atomic'
                    api['llm_reason'] = assignment.get('reason', '')
                    print(f"  [{i}] ATOMIC: {assignment.get('reason', '')}")
            else:
                # No assignment from LLM, keep original
                api['cluster_type'] = 'atomic'
                print(f"  [{i}] No assignment, keeping as atomic")

        return scattered_apis

    def _build_api_summary(self, apis: List[Dict[str, Any]]) -> str:
        """Build a concise summary of APIs for LLM."""
        lines = []
        for i, api in enumerate(apis):
            method = api.get('method', 'GET')
            path = api.get('path', '')
            entity = api.get('entity_anchor', 'unknown')

            # Extract key info from path
            path_parts = path.split('/')[-2:]  # Last 2 segments
            path_summary = '/'.join(path_parts)

            lines.append(f"{i}. [{method}] {path_summary} (entity: {entity})")

        return '\n'.join(lines)

    def _build_cluster_summary(self, clusters: List[Dict[str, Any]]) -> str:
        """Build a summary of stable clusters for LLM."""
        lines = []
        for cluster in clusters:
            cluster_id = cluster['cluster_id']
            entity = cluster['entity']
            size = cluster['size']

            # Sample APIs
            sample_apis = cluster['apis'][:3]
            api_samples = []
            for api in sample_apis:
                method = api.get('method', 'GET')
                path = api.get('path', '').split('/')[-1]
                api_samples.append(f"{method} .../{path}")

            lines.append(f"Cluster {cluster_id}: {entity} ({size} APIs)")
            lines.append(f"  Examples: {', '.join(api_samples)}")

        return '\n'.join(lines)

    def _build_analysis_prompt(self, scattered_summary: str, stable_summary: str) -> str:
        """Build the prompt for LLM analysis."""
        prompt = f"""You are an API clustering expert. Analyze the following scattered APIs and decide how to group them.

SCATTERED APIs (need classification):
{scattered_summary}

EXISTING STABLE CLUSTERS:
{stable_summary}

For each scattered API, decide ONE of the following:
1. MERGE: Merge into an existing cluster (if semantically related)
2. GROUP: Group with other scattered APIs to form a new cluster
3. ATOMIC: Keep as standalone (if truly unique)

Provide your analysis in JSON format:
{{
  "assignments": [
    {{
      "api_index": 0,
      "action": "merge|group|atomic",
      "target_cluster": <cluster_id if merge>,
      "new_group_name": "<name if group>",
      "reason": "<brief explanation>"
    }}
  ],
  "new_groups": [
    {{
      "group_name": "<name>",
      "api_indices": [<list of indices>],
      "reason": "<why these belong together>"
    }}
  ]
}}

Guidelines:
- Statistics APIs (time-summary, dashboard, etc.) should be grouped together
- Simple-list APIs should be grouped together
- Upload/download utilities should be grouped together
- Status update APIs should be grouped with their main entity if possible
- Only create new groups if there's clear semantic cohesion (3+ APIs)
"""
        return prompt

    def _call_llm(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call LLM API based on provider."""
        print(f"Using LLM provider: {self.llm_provider}")
        print(f"Model: {self.model}")

        if self.llm_provider == "rule":
            return self._fallback_analysis(scattered_apis)
        elif self.llm_provider == "openai":
            return self._call_openai(prompt, scattered_apis)
        elif self.llm_provider == "qwen":
            return self._call_qwen(prompt, scattered_apis)
        elif self.llm_provider == "deepseek":
            return self._call_deepseek(prompt, scattered_apis)
        elif self.llm_provider == "zhipu":
            return self._call_zhipu(prompt, scattered_apis)
        elif self.llm_provider == "ollama":
            return self._call_ollama(prompt, scattered_apis)
        elif self.llm_provider == "openai-compatible":
            return self._call_openai_compatible(prompt, scattered_apis)
        else:
            print(f"Unknown provider: {self.llm_provider}, using rule-based fallback")
            return self._fallback_analysis(scattered_apis)

    def _call_openai(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call OpenAI API."""
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an API clustering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return self._fallback_analysis(scattered_apis)

    def _call_qwen(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call Alibaba Qwen API (DashScope)."""
        try:
            import openai

            # Qwen uses OpenAI-compatible API
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an API clustering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Qwen: {e}")
            return self._fallback_analysis(scattered_apis)

    def _call_deepseek(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call DeepSeek API."""
        try:
            import openai

            # DeepSeek uses OpenAI-compatible API
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an API clustering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling DeepSeek: {e}")
            return self._fallback_analysis(scattered_apis)

    def _call_zhipu(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call Zhipu AI (GLM) API."""
        try:
            from zhipuai import ZhipuAI

            client = ZhipuAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an API clustering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content
        except ImportError:
            print("zhipuai package not installed. Install with: pip install zhipuai")
            print("Falling back to OpenAI-compatible API...")
            try:
                import openai
                client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an API clustering expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error calling Zhipu: {e}")
                return self._fallback_analysis(scattered_apis)
        except Exception as e:
            print(f"Error calling Zhipu: {e}")
            return self._fallback_analysis(scattered_apis)

    def _call_ollama(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call local Ollama API."""
        try:
            import requests

            response = requests.post(
                f'{self.api_base}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"Ollama returned status code: {response.status_code}")
                return self._fallback_analysis(scattered_apis)
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")
            return self._fallback_analysis(scattered_apis)

    def _call_openai_compatible(self, prompt: str, scattered_apis: List[Dict[str, Any]]) -> str:
        """Call any OpenAI-compatible API."""
        try:
            import openai

            client = openai.OpenAI(
                api_key=self.api_key or "dummy-key",
                base_url=self.api_base
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an API clustering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI-compatible API: {e}")
            return self._fallback_analysis(scattered_apis)

    def _fallback_analysis(self, scattered_apis: List[Dict[str, Any]]) -> str:
        """Fallback rule-based analysis when LLM is not available."""
        print("\n⚠️  LLM not available, using rule-based fallback analysis...")

        assignments = []
        new_groups = []

        # Group 1: Statistics APIs
        statistics_indices = []
        # Group 2: Simple-list APIs
        simple_list_indices = []
        # Group 3: Upload/Download APIs
        upload_indices = []
        # Group 4: Status update APIs
        status_indices = []

        for i, api in enumerate(scattered_apis):
            path = api.get('path', '').lower()
            entity = api.get('entity_anchor', '').lower()

            # Classify by pattern
            if 'statistics' in entity or 'summary' in path or 'dashboard' in path:
                statistics_indices.append(i)
            elif 'simple-list' in path or entity == 'simple-list':
                simple_list_indices.append(i)
            elif 'upload' in path or 'download' in path or 'export' in path:
                upload_indices.append(i)
            elif 'update-status' in path or 'update-default-status' in path:
                status_indices.append(i)
            else:
                # Keep as atomic
                assignments.append({
                    "api_index": i,
                    "action": "atomic",
                    "reason": "Unique API with no clear grouping pattern"
                })

        # Create groups for categories with 2+ APIs
        if len(statistics_indices) >= 2:
            new_groups.append({
                "group_name": "statistics_reporting",
                "api_indices": statistics_indices,
                "reason": "Statistics and reporting APIs grouped together"
            })
        else:
            for idx in statistics_indices:
                assignments.append({
                    "api_index": idx,
                    "action": "atomic",
                    "reason": "Single statistics API"
                })

        if len(simple_list_indices) >= 2:
            new_groups.append({
                "group_name": "simple_list_utilities",
                "api_indices": simple_list_indices,
                "reason": "Simple list utility APIs grouped together"
            })
        else:
            for idx in simple_list_indices:
                assignments.append({
                    "api_index": idx,
                    "action": "atomic",
                    "reason": "Single simple-list API"
                })

        if len(upload_indices) >= 2:
            new_groups.append({
                "group_name": "file_operations",
                "api_indices": upload_indices,
                "reason": "File upload/download/export APIs grouped together"
            })
        else:
            for idx in upload_indices:
                assignments.append({
                    "api_index": idx,
                    "action": "atomic",
                    "reason": "Single file operation API"
                })

        if len(status_indices) >= 2:
            new_groups.append({
                "group_name": "status_management",
                "api_indices": status_indices,
                "reason": "Status update APIs grouped together"
            })
        else:
            for idx in status_indices:
                assignments.append({
                    "api_index": idx,
                    "action": "atomic",
                    "reason": "Single status update API"
                })

        result = {
            "assignments": assignments,
            "new_groups": new_groups
        }

        print(f"  Created {len(new_groups)} new groups")
        print(f"  Kept {len(assignments)} APIs as atomic")

        return json.dumps(result, indent=2)

    def _parse_llm_response(self, response: str, scattered_apis: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Parse LLM response into assignments."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                assignments = {}

                # Process direct assignments
                for assignment in data.get('assignments', []):
                    api_idx = assignment.get('api_index')
                    if api_idx is not None and 0 <= api_idx < len(scattered_apis):
                        assignments[api_idx] = assignment

                # Process new groups
                next_group_id = 1000  # Start new groups at high ID
                for group in data.get('new_groups', []):
                    for api_idx in group.get('api_indices', []):
                        if 0 <= api_idx < len(scattered_apis):
                            assignments[api_idx] = {
                                'action': 'group',
                                'new_cluster_id': next_group_id,
                                'group_name': group.get('group_name'),
                                'reason': group.get('reason')
                            }
                    next_group_id += 1

                return assignments
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response[:500]}")

        return {}

    def _get_api_key(self, api: Dict[str, Any]) -> str:
        """Generate a unique key for an API."""
        method = api.get('method', 'GET')
        path = api.get('path', '')
        return f"{method}:{path}"
