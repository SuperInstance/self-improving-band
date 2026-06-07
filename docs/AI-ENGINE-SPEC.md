# Turing-tensor-midi AI Engine Spec

## API Configuration (DEFAULTS)

Primary: z.ai GLM-5.1 (https://api.z.ai)
Fallback: DeepInfra Seed-2.0-mini (https://api.deepinfra.com)

NO OpenAI. NO OpenRouter. NO Ollama.

The engine uses an abstract completion interface:

```python
class CompletionProvider(Protocol):
    async def complete(self, messages: list[dict], **kwargs) -> str: ...

class ZAIProvider(CompletionProvider):
    """z.ai GLM-5.1 — primary, unlimited pro plan"""
    
class DeepInfraProvider(CompletionProvider):
    """DeepInfra — supplementary, cheap"""
    # Model roster: Seed-2.0-mini, Gemma-4-31B, Nemotron-120B, Qwen-3.6, Hermes-405B
```

Config in default.yaml:
```yaml
ai:
  primary:
    provider: zai
    model: glm-5.1
    base_url: https://api.z.ai/v1
  fallback:
    provider: deepinfra  
    model: Seed-2.0-mini
    base_url: https://api.deepinfra.com/v1/openai
  max_tokens: 300
  temperature: 0.6
```

Why this matters:
- z.ai is our workhorse — unlimited, fast, good at everything
- DeepInfra is our safety net — pennies per call, dozens of models
- GPU/VRAM stays free for cuda-oxide, tensor operations, parallel agents
- Anyone else can swap providers in config — fully API-agnostic
