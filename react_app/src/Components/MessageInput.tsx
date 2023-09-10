import { Button, Input } from "antd";
import axios from "axios";
import React, { FC, useEffect, useState } from "react";
import { LiveAudioVisualizer } from "react-audio-visualize";
import { useAudioRecorder } from "react-audio-voice-recorder";
import styled from "styled-components";
import { MessageType, SenderEnum, TypeEnum } from "../types/message";
import mic from "../assets/icon/mic.svg";
import { PauseOutlined } from "@ant-design/icons";
import { getCurrentTime } from "../utils/currentTime";
import { sendAudioMessage, sendMessage } from "../api/messageApi";
import { convertBase64 } from "../utils/base64";

const MessageContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  height: 60px;
  padding: 8px 8px 24px 8px;

  background: #e9eaed;
`;

type Props = {
  setNewMessage: (message: MessageType) => void;
  docId: number;
  isAiEnabled: boolean;
};

export const MessageInput: FC<Props> = ({
  setNewMessage,
  docId,
  isAiEnabled,
}) => {
  const recorderControls = useAudioRecorder();
  const [value, setValue] = useState<string>("");

  const addAudioElement = async (blob: Blob) => {
    const res = await sendAudioMessage(blob);
    const newItem = {
      sender: SenderEnum.USER,
      type: TypeEnum.AUDIO,
      date: getCurrentTime(),
      audio: blob,
      text: res.data,
    };
    setNewMessage(newItem);
    const res2 = await sendMessage(res.data, docId, isAiEnabled);
    const binaryString = convertBase64(res2.data.tts_file);
    const newBlob = new Blob([binaryString], {
      type: "audio/wav",
    });
    const serverItem = {
      sender: SenderEnum.SERVER,
      type: TypeEnum.AUDIO,
      text: res2.data.answer,
      date: getCurrentTime(),
      audio: newBlob,
    };
    setNewMessage(serverItem);
  };

  const handleKeyDown = async (event: any) => {
    if (event.key === "Enter") {
      if (event.target.value) {
        const newItem = {
          sender: SenderEnum.USER,
          type: TypeEnum.TEXT,
          text: event.target.value,
          date: getCurrentTime(),
        };
        setNewMessage(newItem);
        setValue("");
        const res = await sendMessage(event.target.value, docId, isAiEnabled);
        const binaryString = convertBase64(res.data.tts_file);
        const blob = new Blob([binaryString], {
          type: "audio/wav",
        });
        const serverItem = {
          sender: SenderEnum.SERVER,
          type: TypeEnum.AUDIO,
          text: res.data.answer,
          date: getCurrentTime(),
          audio: blob,
        };
        setNewMessage(serverItem);
      }
    }
  };

  useEffect(() => {
    if (!recorderControls.recordingBlob) return;
    addAudioElement(recorderControls.recordingBlob);
  }, [recorderControls.recordingBlob]);

  return (
    <MessageContainer>
      <div style={{ width: "100%", height: "100%" }}>
        {recorderControls.mediaRecorder ? (
          <LiveAudioVisualizer
            mediaRecorder={recorderControls.mediaRecorder}
            height={32}
          />
        ) : (
          <Input
            style={{ height: "100%" }}
            placeholder="Type your message"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        )}
      </div>
      <div>
        {recorderControls.isRecording ? (
          <Button
            icon={<PauseOutlined />}
            type="primary"
            shape="circle"
            onClick={recorderControls.stopRecording}
          ></Button>
        ) : (
          <Button
            shape="circle"
            type="primary"
            icon={<img style={{ width: "70%" }} src={mic} alt="icon" />}
            onClick={recorderControls.startRecording}
          ></Button>
        )}
      </div>
    </MessageContainer>
  );
};
