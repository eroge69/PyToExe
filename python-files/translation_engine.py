from transformers import pipeline

# It's good practice to specify the model name explicitly
# For English to Arabic, a common choice is a MarianMT model
# Example: "Helsinki-NLP/opus-mt-en-ar"
# Or a larger model if more nuanced translation is needed and resources allow.
DEFAULT_MODEL_NAME = "Helsinki-NLP/opus-mt-en-ar"

class TranslationEngine:
    def __init__(self, model_name=None):
        """Initializes the translation engine.

        Args:
            model_name (str, optional): The name of the Hugging Face model to use.
                                        Defaults to DEFAULT_MODEL_NAME.
        """
        self.model_name = model_name if model_name else DEFAULT_MODEL_NAME
        self.translator = None
        try:
            # Using device=-1 for CPU, change to 0, 1, etc., for GPU if available and configured
            self.translator = pipeline("translation", model=self.model_name, device=-1)
            print(f"Translation model 	'{self.model_name}	' loaded successfully.")
        except Exception as e:
            print(f"Error loading translation model 	'{self.model_name}	': {e}")
            print("Please ensure you have an internet connection to download the model initially,")
            print("and that the model name is correct. You might need to install PyTorch or TensorFlow.")
            # Fallback or error handling can be more sophisticated here

    def translate_text(self, text_to_translate, src_lang="en", target_lang="ar"):
        """Translates a single string of text.

        Args:
            text_to_translate (str): The text to translate.
            src_lang (str): Source language code (e.g., 'en'). Not always used by all models.
            target_lang (str): Target language code (e.g., 'ar'). Not always used by all models.

        Returns:
            str: The translated text, or None if translation fails.
        """
        if not self.translator:
            print("Translator not initialized. Cannot translate.")
            return None
        
        if not text_to_translate or not isinstance(text_to_translate, str):
            print("Invalid text input for translation.")
            return None

        try:
            # Some models might not need src_lang and target_lang explicitly if they are bilingual by design
            # The pipeline for "translation_xx_to_yy" usually handles this implicitly.
            # For a generic "translation" pipeline, you might need to specify target_language.
            # However, for Helsinki-NLP models, the model name itself defines the language pair.
            result = self.translator(text_to_translate)
            if result and isinstance(result, list) and len(result) > 0 and "translation_text" in result[0]:
                return result[0]["translation_text"]
            else:
                print(f"Unexpected translation result format: {result}")
                return None
        except Exception as e:
            print(f"Error during translation: {e}")
            return None

    def translate_batch(self, texts_to_translate, src_lang="en", target_lang="ar"):
        """Translates a batch of texts.

        Args:
            texts_to_translate (list): A list of strings to translate.
            src_lang (str): Source language code.
            target_lang (str): Target language code.

        Returns:
            list: A list of translated strings. Returns None for failed translations in the batch.
        """
        if not self.translator:
            print("Translator not initialized. Cannot translate batch.")
            return [None] * len(texts_to_translate)
        
        if not texts_to_translate or not isinstance(texts_to_translate, list):
            print("Invalid batch input for translation.")
            return []

        try:
            results = self.translator(texts_to_translate)
            translated_texts = []
            for result in results:
                if result and isinstance(result, dict) and "translation_text" in result:
                    translated_texts.append(result["translation_text"])
                else:
                    print(f"Unexpected translation result format in batch: {result}")
                    translated_texts.append(None)
            return translated_texts
        except Exception as e:
            print(f"Error during batch translation: {e}")
            return [None] * len(texts_to_translate)

if __name__ == '__main__':
    # Example Usage for testing
    print("Initializing Translation Engine...")
    # Ensure 'transformers' and a backend like 'torch' or 'tensorflow' are installed.
    # pip install transformers torch
    engine = TranslationEngine() # Uses default Helsinki-NLP/opus-mt-en-ar

    if engine.translator:
        print("\nTesting single text translation:")
        english_text_single = "Hello, how are you today?"
        arabic_translation_single = engine.translate_text(english_text_single)
        if arabic_translation_single:
            print(f"English: {english_text_single}")
            print(f"Arabic: {arabic_translation_single}")
        else:
            print("Single text translation failed.")

        print("\nTesting batch text translation:")
        english_texts_batch = [
            "This is the first sentence.",
            "This is another sentence for translation.",
            "Baldur's Gate 3 is a great game."
        ]
        arabic_translations_batch = engine.translate_batch(english_texts_batch)
        
        if arabic_translations_batch:
            for i, text in enumerate(english_texts_batch):
                print(f"English: {text}")
                print(f"Arabic: {arabic_translations_batch[i] if arabic_translations_batch[i] else 'Translation failed'}")
        else:
            print("Batch text translation failed.")
    else:
        print("Translation engine could not be initialized. Skipping tests.")


