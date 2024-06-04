import re
import logging
import torch
from peft import PeftModel, PeftConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from accelerate import infer_auto_device_map


logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


class LLMHandler:
    def __init__(
        self,
        model_path,
        generation_params,
        prompt_instruction=None,
        bits_and_bytes_config=None,
        adapter_path=None,
    ):
        self.prompt_instruction = prompt_instruction
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.generation_params = generation_params
        self._generate_bits_and_bytes(bits_and_bytes_config)
        self._load_model(model_path, adapter_path)
        self._print_state()

    def _generate_bits_and_bytes(self, quantization_config):

        if quantization_config:
            quantization_config["bnb_4bit_compute_dtype"] = torch.float16
            self.quantization = BitsAndBytesConfig(**quantization_config)
        else:
            self.quantization = None

    def _load_model(self, model_path, adapter_path):

        # Load the Lora model
        if adapter_path:
            config = PeftConfig.from_pretrained(adapter_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                quantization_config=self.quantization,
                device_map=self.device,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                config.base_model_name_or_path
            )
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
        # If no adapter_path load base model
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                low_cpu_mem_usage=True,
                device_map=self.device,
                quantization_config=self.quantization,
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def _print_state(self):
        """
        Print the device information
        """
        # Check cuda
        print("Using self.device:", self.device)
        print()

        # Additional Info when using cuda
        if self.device.type == "cuda":
            print(torch.cuda.get_device_name(0))
            print("Memory Usage:")
            print(
                "Allocated:", round(torch.cuda.memory_allocated(0) / 1024**3, 1), "GB"
            )
            print("Cached:   ", round(torch.cuda.memory_reserved(0) / 1024**3, 1), "GB")

    def _check_prompt_instruction(self, prompt_instruction):
        if self.prompt_instruction is None:
            if prompt_instruction:
                return prompt_instruction
            else:
                raise Exception("No prompt instruction message given")
        if self.prompt_instruction:
            if prompt_instruction is None:
                return self.prompt_instruction
            else:
                raise Exception(
                    "Passed instruction in the init and in the method, need to remove one"
                )

    def construct_prompt(self, prompt_instruction, text):
        return f"{prompt_instruction}\n{text}"

    def encode_input(self, message):
        inputs = self.tokenizer(message, return_tensors="pt").to(self.device)
        return inputs

    def generate_output(self, encoded):
        generation_output = self.model.generate(**encoded, **self.generation_params)
        return generation_output

    def decode_output(self, generation_output):
        token_output = generation_output[0]
        text_output = self.tokenizer.decode(token_output)
        return text_output

    def separate_prompt_and_answer(self, inputs, output):

        prompt_length = inputs['input_ids'].shape[1]
        prompt_context = self.tokenizer.decode(output[0][0:prompt_length])
        answer = self.tokenizer.decode(output[0][prompt_length:])
        return prompt_context, answer

    def passing_article_to_llm(self, text, prompt_instruction=None):
        prompt_instruction = self._check_prompt_instruction(prompt_instruction)
        prompt_message = self.construct_prompt(prompt_instruction, text)

        inputs = self.encode_input(prompt_message)

        output = self.generate_output(inputs)
        # text_output = self.decode_output(generation_output)
        prompt_context, answer = self.separate_prompt_and_answer(inputs, output)

        return prompt_context, answer


class LLMHandlerInstruct(LLMHandler):

    def generate_output(self, encoded):
        generation_output = self.model.generate(encoded, **self.generation_params)
        return generation_output

    def encode_input(self, message):

        messages = [{"role": "user", "content": message}]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.device)
        return inputs

    def separate_prompt_and_answer(self, inputs, output):
        token_output = output[0]
        text_output = self.tokenizer.decode(token_output)
        pattern = re.compile(r"\[INST\]\s*(.*?)\s*\[/INST\](.*)", re.DOTALL)
        match = pattern.match(text_output)
        if match:
            prompt_context = match.group(1).strip()
            answer = match.group(2).strip()
            return prompt_context, answer
        else:
            return None, text_output.strip()


def main():

    # Define model_path, generation_params, and prompt_instruction
    model = "./llm_models/mistral_7b_v01"

    generation_params = {
        # "context_size": 2048,
        "temperature": 0.1,
        "do_sample": True,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": 50,
        "repetition_penalty": 1.1,
    }

    prompt_instruction = "Your prompt instruction here"

    llm_handler = LLMHandler(
        model,
        generation_params,
        prompt_instruction=prompt_instruction,
    )
    methods = "Your method section text here"  # Define your method section text
    # text_output, prompt_text, answer = llm_handler.passing_article_to_llm(methods)
    text_output = llm_handler.passing_article_to_llm(methods)
    # print("PROMPT CONTEXT:\n")
    # print(prompt_text)
    # print("\n")
    # print("GENERATED ANSWER:\n")
    # print(answer)
    # print("\n")
    print("TEXT OUTPUT:\n")
    print(text_output)


if __name__ == "__main__":
    main()
