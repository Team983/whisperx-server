cd .. && rm whisperx-server.zip || zip -r whisperx-server.zip ./* && git add . && git commit -m "Fix: zip file" && git push origin master