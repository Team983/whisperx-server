# For all models except for prompt-tuned models
cd ..
ct2-transformers-converter --model /home/team983/server/whisperx-server/models/software-development --output_dir /home/team983/server/whisperx-server/models/software-development-2 \
    --copy_files tokenizer.json --quantization float16 