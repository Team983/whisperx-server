def assign_new_speakers(result):
        new_result = {'language':result['language'], 'segments':[]}
        speakers = []
        for segment in result['segments']:
            text = preprocess_transcription(segment['text'])
            if len(text) != 0:
                segment['text'] = text
                new_result['segments'].append(segment)
                speaker = segment['speaker']
                if speaker not in speakers:
                    speakers.append(speaker)

        new_speakers = {}
        for i in range(1, len(speakers)+1):
            new_speakers[speakers[i-1]] = f'발화자 {i}'

        for segment in new_result['segments']:
            segment['speaker'] = new_speakers[segment['speaker']]
        return new_result


def preprocess_transcription(transcription:str):
    transcription = transcription.strip()
    if transcription.startswith('MBC 뉴스') and len(transcription) in range(13, 16):
        transcription = '...'
    return transcription