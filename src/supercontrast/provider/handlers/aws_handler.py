import boto3

from supercontrast.provider.provider_enum import Provider
from supercontrast.provider.provider_handler import ProviderHandler
from supercontrast.task import (
    OCRRequest,
    OCRResponse,
    SentimentAnalysisRequest,
    SentimentAnalysisResponse,
    Task,
    TranslationRequest,
    TranslationResponse,
)
from supercontrast.utils.text import truncate_text

# models
class AWSSentimentAnalysis(ProviderHandler):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        super().__init__(provider=Provider.AWS, task=Task.SENTIMENT_ANALYSIS)
        self.client = boto3.client("comprehend", 
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   aws_session_token=aws_session_token)
        self.THRESHOLD = 0

    def request(self, request: SentimentAnalysisRequest) -> SentimentAnalysisResponse:
        response = self.client.detect_sentiment(
            Text=truncate_text(request.text), LanguageCode="en"
        )
        score = (
            response["SentimentScore"]["Positive"]
            - response["SentimentScore"]["Negative"]
        )

        return SentimentAnalysisResponse(score=score)

    def get_name(self) -> str:
        return "Aws Comprehend - Sentiment Analysis"

    @classmethod
    def init_from_env(cls, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None) -> "AWSSentimentAnalysis":
        return cls(aws_access_key_id, aws_secret_access_key, aws_session_token)


class AWSTranslate(ProviderHandler):
    def __init__(self, src_language: str, target_language: str, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        super().__init__(provider=Provider.AWS, task=Task.TRANSLATION)
        self.client = boto3.client("translate",
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   aws_session_token=aws_session_token)
        self.src_language = src_language
        self.target_language = target_language

    def request(self, request: TranslationRequest) -> TranslationResponse:
        response = self.client.translate_text(
            Text=truncate_text(request.text),
            SourceLanguageCode=self.src_language,
            TargetLanguageCode=self.target_language,
        )
        translated_text = response["TranslatedText"]

        result = TranslationResponse(
            text=translated_text,
        )

        return result

    def get_name(self) -> str:
        return "AWS Translate"

    @classmethod
    def init_from_env(
        cls, source_language: str, target_language: str, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None
    ) -> "AWSTranslate":
        return cls(source_language, target_language, aws_access_key_id, aws_secret_access_key, aws_session_token)


class AWSOCR(ProviderHandler):
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
        super().__init__(provider=Provider.AWS, task=Task.OCR)
        self.client = boto3.client("textract",
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   aws_session_token=aws_session_token)

    def request(self, request: OCRRequest) -> OCRResponse:
        if isinstance(request.image, str):
            with open(request.image, "rb") as image_file:
                image_data = image_file.read()
        else:
            image_data = request.image

        response = self.client.analyze_document(
            Document={"Bytes": image_data}, FeatureTypes=["FORMS", "TABLES"]
        )

        extracted_text = ""
        for item in response.get("Blocks", []):
            if item["BlockType"] == "LINE":
                extracted_text += item["Text"] + "\n"

        return OCRResponse(text=extracted_text.strip())

    def get_name(self) -> str:
        return "AWS Textract - OCR"

    @classmethod
    def init_from_env(cls, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None) -> "AWSOCR":
        return cls(aws_access_key_id, aws_secret_access_key, aws_session_token)


# factory


def aws_provider_factory(task: Task, **config) -> ProviderHandler:
    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    aws_session_token = config.get("aws_session_token")

    if task == Task.SENTIMENT_ANALYSIS:
        return AWSSentimentAnalysis.init_from_env(aws_access_key_id, aws_secret_access_key, aws_session_token)
    elif task == Task.TRANSLATION:
        source_language = config.get("source_language", "en")
        target_language = config.get("target_language", "es")
        return AWSTranslate.init_from_env(
            source_language=source_language, 
            target_language=target_language,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
    elif task == Task.OCR:
        return AWSOCR.init_from_env(aws_access_key_id, aws_secret_access_key, aws_session_token)
    else:
        raise ValueError(f"Unsupported task: {task}")
