def preprocess_transcription(transcription:str):
    transcription = transcription.strip()
    if transcription.startswith('MBC 뉴스') and len(transcription) in range(13, 16):
        transcription = '...'
    return transcription