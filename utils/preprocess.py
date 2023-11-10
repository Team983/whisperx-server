def preprocess_transcription(transcription:str):
    assert isinstance(transcription, str)
    transcription = transcription.strip()
    print(f'Current transcription of segment: {transcription}')
    if transcription.startswith('MBC 뉴스') and len(transcription) in range(13, 16):
        transcription = ''
    print(f'Preprocessed transcription of segment: {transcription}')
    return transcription