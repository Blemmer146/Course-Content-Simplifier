from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.prompts import PromptTemplateManager


def setup_watsonx(api_key, project_id, region):
    """Setup Watsonx.ai client and model inference"""
    url = f"https://{region}.ml.cloud.ibm.com"
    credentials = Credentials(api_key=api_key, url=url)

    client = APIClient(credentials)
    client.set.default_project(project_id)

    model_inference = ModelInference(
        model_id="ibm/granite-3-8b-instruct",
        credentials=credentials,
        project_id=project_id
    )

    prompt_mgr = PromptTemplateManager(
        credentials=credentials,
        project_id=project_id
    )

    return client, model_inference, prompt_mgr