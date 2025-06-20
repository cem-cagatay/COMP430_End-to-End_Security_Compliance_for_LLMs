# Secure Chat Assistant with Malicious Prompt Detection and Role-Based Access Control
📣 **In the project report, we demonstrated outputs of the application from the version in the pipeline_v2 branch. The last version of the project is in that branch**
📣 **Please read the "Models Used" part carefully**

Note: The .env file is intentionally excluded from this repository for security reasons. The endpoint URLs and API tokens are provided in the project report.
OPENAI_API_KEY=yopenai_key
HF_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/model-name
HF_TOKEN = hf_token

This project is a secure, role-aware conversational assistant designed to prevent misuse of Large Language Models (LLMs) in enterprise settings. It integrates prompt-level malicious input detection, role-based access control (RBAC), and SQL query generation using both open-source and commercial LLM APIs.

## Project Overview

Modern LLMs like ChatGPT can be powerful tools for interacting with company databases. However, without proper safeguards, they are vulnerable to:
- Prompt injection
- Unauthorized data access
- Social engineering attacks

To address these threats, we designed a **multi-layered pipeline**:
1. **Malicious Prompt Detection** using our fine-tuned Zephyr model.
2. **RBAC Enforcement** that checks user permissions before generating SQL.
3. **Secure SQL Generation** powered by ChatGPT (OpenAI).

---

## Features

- Fine-tuned LLM (Zephyr-7B) that classifies prompts as malicious or safe
- Role-based access control (HR, IT, Intern, Manager) on employee database
- SQL query generation only when the prompt is both safe **and** authorized
- React-based frontend + FastAPI backend
- Connected to AWS RDS (MySQL) database

---

## Models Used

### 🔹 Base LLM (Main Branch)
- **Model**: [HuggingFaceH4/zephyr-7b-beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)
- **Branch**: `main`
- This model is unmodified and is used to explore base-level performance.

### 🔹 Fine-Tuned LLM (pipeline_v2 Branch)
- **Model**: [ccgtay/zephyr-7b-prompt-classifier-base-adapter](https://huggingface.co/ccgtay/zephyr-7b-prompt-classifier-base-adapter/tree/main)
- **Branch**: `pipeline_v2`
- This model is fine-tuned using the [safe-guard-prompt-injection dataset](https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection) to detect adversarial prompts.
- Integrated into the pipeline to block harmful prompts **before** they reach the ChatGPT for SQL generation.

---
