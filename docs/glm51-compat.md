# Zhipu GLM Compatibility

Use `configs/experiments/exp-simple-code-glm51.yaml` when running AHE with Zhipu GLM through the OpenAI-compatible Chat Completions endpoint.

Set these environment variables before launch:

```dotenv
ZHIPU_LLM_API_KEY="your-zhipu-api-key"
# Optional. If omitted, AHE uses https://open.bigmodel.cn/api/paas/v4/
ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

Do not put the API key in YAML files, Python code, logs, or committed examples.

The compatibility layer in `evolve.py` handles provider differences before NexAU YAML patches are applied:

- uses `openai_chat_completion` instead of `openai_responses`;
- defaults the model to `glm-5.1` only when a Zhipu provider config omits a GLM model name;
- normalizes Z.AI / BigModel base URLs to a client base URL rather than a full `/chat/completions` URL;
- passes GLM-specific request options through OpenAI SDK `extra_body`, including `thinking` and streamed `tool_stream`;
- removes OpenAI Responses-only `reasoning` fields from GLM requests;
- applies the same compatibility fields to Agent Debugger LLM settings.

The bundled overlay currently sets `model: "glm-5.1"` and disables thinking by default:

```yaml
zai_compat:
  thinking:
    type: "disabled"
```

If you need to turn thinking on, override it in the overlay:

```yaml
zai_compat:
  thinking:
    type: "enabled"
```

If you need to force GLM sampling behavior, set `zai_compat.do_sample` explicitly. The bundled overlay omits it and uses the provider default.
