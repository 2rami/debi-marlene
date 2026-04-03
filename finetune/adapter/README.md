---
library_name: peft
license: other
base_model: Qwen2.5-Omni-7B/thinker
tags:
- base_model:adapter:Qwen2.5-Omni-7B/thinker
- llama-factory
- lora
- transformers
pipeline_tag: text-generation
model-index:
- name: debi-marlene
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# debi-marlene

This model is a fine-tuned version of [Qwen/Qwen2.5-Omni-7B](https://huggingface.co/Qwen/Qwen2.5-Omni-7B) on the debi-marlene dataset.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 5e-05
- train_batch_size: 2
- eval_batch_size: 8
- seed: 42
- gradient_accumulation_steps: 2
- total_train_batch_size: 4
- optimizer: Use OptimizerNames.ADAMW_TORCH_FUSED with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: cosine
- lr_scheduler_warmup_ratio: 0.05
- num_epochs: 10

### Training results



### Framework versions

- PEFT 0.17.1
- Transformers 4.57.1
- Pytorch 2.10.0+cu128
- Datasets 4.0.0
- Tokenizers 0.22.2