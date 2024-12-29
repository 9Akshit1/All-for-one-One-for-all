import logging
import json
import numpy as np
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import torch


def numpy_serializer(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def Generate_Main(all_extracted_info):
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        report_text = ""
        for info in all_extracted_info:
            query = info.get('query', 'No query')
            report_text += f"Query: {query}\n"

            for result in info.get('results', []):
                score = float(result.get('score', 'N/A')) if hasattr(result.get('score'), '__float__') else result.get('score')
                report_text += f"Relevant Snippet (Score: {score}): {result.get('text', '')}\n"

            report_text += "\n---\n\n"

        output_report_filepath = "application_writer/generated_report.txt"
        with open(output_report_filepath, "w", encoding='utf-8') as file:
            file.write(report_text)

        output_json_filepath = "application_writer/generated_report.json"
        with open(output_json_filepath, "w", encoding='utf-8') as file:
            json.dump(all_extracted_info, file, indent=2, default=numpy_serializer)

        logger.info(f"Report generated and saved to {output_report_filepath}")
        logger.info(f"JSON report saved to {output_json_filepath}")

        input_file = "application_writer/generated_report.json"

        if os.path.exists(input_file):
            print("Generating paragraph answers...")
            return generate_paragraph_answers(input_file)
        else:
            print(f"Input file '{input_file}' not found. Please ensure the report is generated.")

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return ""


def format_report(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)

        answers = []
        for query_block in report:
            query = query_block.get("query", "No query found")
            answers.append(f"**Query:** {query}\n")

            results = query_block.get("results", [])
            for idx, result in enumerate(results, 1):
                source = result.get("source", "Unknown source")
                text = result.get("text", "").strip()
                answers.append(f"{idx}. Source: {source}\n   {text}\n")

        formatted_text = "\n\n".join(answers)
        print(formatted_text)

    except Exception as e:
        print(f"Error formatting report: {e}")

def gpt2_model_load():
    model_name = "gpt2"
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    return tokenizer, model

def flan_t5_model_load():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        device_map="auto"  # Adjust device usage automatically
    )
    return tokenizer, model

def llama_model_load():
    model_name = "meta-llama/Llama-2-7b-chat-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto"  # Adjust device usage automatically
    )
    return tokenizer, model

def generate_paragraph_answers(json_file):
    try:
        tokenizer, model = gpt2_model_load()

        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)

        paragraph_responses = {}
        for query_block in report:
            query = query_block.get("query", "No query found")
            results = query_block.get("results", [])
            context = " ".join(result.get("text", "").strip() for result in results)

            if context:
                input_text = f"""
                **Task:** Based on the provided context below, please answer the question below in a well-structured, comprehensive, and grammatically correct paragraph. 
                Ensure the response is coherent, clear, and free of errors. Avoid adding any unrelated or fake details. The answer should be complete and logically consistent, summarizing the key points from the context.
                **Context:** {context}
                **Question:** {query}?
                """.strip()
                #print(input_text)
                inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)

                attention_mask = torch.ones(inputs.shape, dtype=torch.long)
                output = model.generate(
                    inputs, attention_mask=attention_mask, pad_token_id=tokenizer.eos_token_id, max_new_tokens=500,
                    num_return_sequences=1, num_beams=2, no_repeat_ngram_size=2, early_stopping=True)

                # Decode only the generated tokens, excluding the input tokens
                generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
                #print(generated_text)
                response_start_index = len(input_text.strip()) + 1  # The index right after the input. This is fro the gpt2 model only
                answer = generated_text[response_start_index:].strip()  # Trim the start of the generated text
                #print("\n**Answer:**", answer)
                response = answer
                paragraph_responses[query + "?"] = response
            else:
                response = f"**Question:** {query}\n**Answer:** No relevant information found.\n"
                response = response[response.find("* * **Questions:*"):]
                paragraph_responses[query + "?"] = response

        for response in list(paragraph_responses.values()):
            print("\nResponse:", response)
        return paragraph_responses

    except Exception as e:
        print(f"Error generating paragraph answers: {e}")
