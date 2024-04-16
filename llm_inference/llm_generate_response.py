import re
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


class LLMHandler:
    def __init__(self, model_path, generation_params, prompt_instruction):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, low_cpu_mem_usage=True, device_map=self.device
        )
        self.generation_params = generation_params
        self.prompt_instruction = prompt_instruction
        self._print_state()

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

    def build_prompt_content(self, method_section_txt):
        start_content = "In the following text:\n"
        content = f"{start_content}{method_section_txt}"
        return content

    def construct_chat_message(self, prompt_content):
        return f"{self.prompt_instruction}\n{prompt_content}"

    def encode_chat_messages(self, messages):
        encoded = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.device)
        return encoded

    def generate_output(self, encoded):
        generation_output = self.model.generate(encoded, **self.generation_params)
        return generation_output

    def decode_output(self, generation_output):
        token_output = generation_output[0]
        text_output = self.tokenizer.decode(token_output)
        return text_output

    def separate_prompt_and_answer(self, text_output):
        pattern = re.compile(r"\[INST\]\s*(.*?)\s*\[/INST\](.*)", re.DOTALL)
        match = pattern.match(text_output)
        if match:
            prompt_context = match.group(1).strip()
            answer = match.group(2).strip()
            return prompt_context, answer
        else:
            return None, text_output.strip()

    def passing_article_to_llm(self, text):
        prompt_content = self.build_prompt_content(text)
        prompt_message = self.construct_chat_message(prompt_content)
        messages = [{"role": "user", "content": prompt_message}]

        encoded = self.encode_chat_messages(messages)
        generation_output = self.generate_output(encoded)
        text_output = self.decode_output(generation_output)
        prompt_context, answer = self.separate_prompt_and_answer(text_output)

        return prompt_context, answer


def main():

    # Define model_path, generation_params, and prompt_instruction
    model = "./llm_models/mistral_7b_instruct_v02"

    generation_params = {
        "context_size": 2048,
        "temperature": 0,
        "do_sample": True,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": 512,
        "repetition_penalty": 1.1,
    }

    prompt_instruction = "Your prompt instruction here"

    llm_handler = LLMHandler(model, generation_params, prompt_instruction)
    methods = "Your method section text here"  # Define your method section text
    prompt_text, answer = llm_handler.passing_article_to_llm(methods)
    print('PROMPT CONTEXT:\n')
    print(prompt_text)
    print('\n')
    print('GENERATED ANSWER:\n')
    print(answer)
    print('\n')


if __name__ == "__main__":
    main()
