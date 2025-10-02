from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("distilbert/distilgpt2")
model = AutoModelForCausalLM.from_pretrained("distilbert/distilgpt2")

input_text = "Write me a poem about a sunset."
input_ids = tokenizer(input_text, return_tensors="pt")["input_ids"]
attention_mask = torch.ones_like(input_ids)

outputs = model.generate(
    input_ids,
    attention_mask=attention_mask,
    min_new_tokens=50,      
    max_new_tokens=150,     
    do_sample=True,         # enable sampling for variety
    top_p=0.9,              # nucleus sampling
    top_k=50,               # limit top-k tokens
    no_repeat_ngram_size=2, # avoid repeated n-grams
    pad_token_id=tokenizer.eos_token_id,
)
print(tokenizer.decode(outputs[0], skip_special_tokens=True).strip())