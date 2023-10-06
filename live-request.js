const fs = require('fs');
const WebSocket = require('ws');

// WAV 파일 경로 설정
// /home/team983/server/data/audio/example_1.wav
// /home/team983/server/data/audio/example_5.mov
// /home/team983/server/data/audio/example_15.m4a
// /home/team983/server/data/audio/example_30.wav
const audioFilePath = '/home/team983/server/data/audio/example_5.mov';

// 사용자 이름 설정
const userId = "yongchan";

// WebSocket 서버 URL로 대체해야 합니다.
const serverUrl = "ws://220.118.70.197:8081/live";

// WebSocket 연결
const socket = new WebSocket(serverUrl);

socket.on('message', (data) => {

  // 서버에서 보낸 데이터를 JSON으로 파싱
  const receivedData = JSON.parse(data);

  // 데이터 처리 및 추가 작업 수행
  console.log(receivedData.result.segments)

  // WebSocket 연결 닫기 (선택사항)
  // socket.close();
});


// socket.on('open', () => {
//   console.log('WebSocket 연결이 열렸습니다.');

//   // WAV 파일 읽기
//   fs.readFile(audioFilePath, (err, audioData) => {
//     if (err) {
//       console.error('WAV 파일 읽기 오류:', err);
//       return;
//     }

//     // WAV 데이터를 Blob으로 변환
//     const audioArray = Array.from(new Uint8Array(audioData));
    
//     const dataToSend = JSON.stringify({
//       "userId": userId,
//       "audioData": audioArray,
//     });

//     // Blob 데이터를 서버로 전송
//     socket.send(dataToSend);

//     console.log('Blob 데이터를 성공적으로 보냈습니다.');

//     // WebSocket 연결 닫기
//     // socket.close();
//   });
// });

socket.on('open', () => {
  console.log('WebSocket 연결이 열렸습니다.');

  // WAV 파일 읽기
  fs.readFile(audioFilePath, (err, audioData) => {
    if (err) {
      console.error('WAV 파일 읽기 오류:', err);
      return;
    }

    const audioArray = new Uint8Array(audioData);; // 실제 오디오 데이터를 배열로 대체해야 합니다.
    repeatSend(40, audioArray);

    console.log('Blob 데이터를 성공적으로 보냈습니다.');

    // WebSocket 연결 닫기
    // socket.close();
  });
});


socket.on('close', () => {
  console.log('WebSocket 연결이 닫혔습니다.');
});

socket.on('error', (error) => {
  console.error('WebSocket 오류:', error);
});


function repeatSend(count, audioArray) {
  if (count <= 0) {
    console.log('모든 작업 완료');
    socket.close();
    return;
  }

  // audioArray를 전송하고 3초 동안 대기
  socket.send(audioArray);

  setTimeout(() => {
    console.log(`작업 ${count} 완료`);
    repeatSend(count - 1, audioArray); // 다음 반복 작업 시작
  }, 1000); 
}