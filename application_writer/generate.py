import logging
import json
import numpy as np
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer
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

        output_report_filepath = "generated_report.txt"
        with open(output_report_filepath, "w", encoding='utf-8') as file:
            file.write(report_text)

        output_json_filepath = "generated_report.json"
        with open(output_json_filepath, "w", encoding='utf-8') as file:
            json.dump(all_extracted_info, file, indent=2, default=numpy_serializer)

        logger.info(f"Report generated and saved to {output_report_filepath}")
        logger.info(f"JSON report saved to {output_json_filepath}")

        return report_text

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


def generate_paragraph_answers(json_file):
    try:
        model_name = "gpt2"
        model = GPT2LMHeadModel.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)

        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)

        paragraph_responses = []
        for query_block in report:
            query = query_block.get("query", "No query found")
            results = query_block.get("results", [])
            context = " ".join(result.get("text", "").strip() for result in results)

            if context:
                input_text = f"""
                **Question:** {query}
                **Context:** {context}
                **Task:** Based on the provided context, please answer the question in a well-structured, comprehensive, and grammatically correct paragraph. 
                Ensure the response is coherent, clear, and free of errors. The answer should be complete and logically consistent, summarizing the key points from the context.
                """

                inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
                attention_mask = torch.ones(inputs.shape, dtype=torch.long)
                output = model.generate(
                    inputs, attention_mask=attention_mask, pad_token_id=tokenizer.eos_token_id,
                    max_length=1024, num_return_sequences=1, num_beams=2, no_repeat_ngram_size=2, early_stopping=True
                )

                answer = tokenizer.decode(output[0], skip_special_tokens=True).strip()
                response = f"**Question:** {query}\n**Answer:** {answer}\n"

                # Remove everything before * * **Questions:*
                response = response[response.find("* * **Questions:*"):]
                paragraph_responses.append(response)

            else:
                response = f"**Question:** {query}\n**Answer:** No relevant information found.\n"
                response = response[response.find("* * **Questions:*"):]
                paragraph_responses.append(response)

        for response in paragraph_responses:
            print(response)
        

    except Exception as e:
        print(f"Error generating paragraph answers: {e}")


input_file = "generated_report.json"

if os.path.exists(input_file):
    print("Generating paragraph answers...")
    generate_paragraph_answers(input_file)
else:
    print(f"Input file '{input_file}' not found. Please ensure the report is generated.")
