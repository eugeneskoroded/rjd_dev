import React, { FC } from "react";
import styled from "styled-components";
import { MessageType, SenderEnum, TypeEnum } from "../types/message";
import { AudioVisualizer } from "react-audio-visualize";

const ChatWrapper = styled.div`
  padding: 8px 8px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  background: #babbbd;
`;

const ChatList = styled.div`
  max-height: 750px;
  /* max-height: 90%; */
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
`;

const MessageItem = styled.div<{ isServer: boolean }>`
  background: #ffffffed;
  border-radius: 8px;
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-wrap: wrap;
  max-width: 80%;
  min-width: 40px;
  ${({ isServer }) => {
    if (isServer) {
      return "align-self:flex-start";
    }

    return "align-self:flex-end";
  }}
`;

type Props = {
  messages: MessageType[];
};

export const ChatContainer: FC<Props> = ({ messages }) => {
  return (
    <ChatWrapper>
      <ChatList>
        {messages.map((el, index) => (
          <MessageItem isServer={el.sender === SenderEnum.SERVER} key={index}>
            {el.type === TypeEnum.AUDIO ? (
              <div
                style={{
                  width: "100%",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <AudioVisualizer
                  blob={el.audio as Blob}
                  width={500}
                  height={75}
                  barWidth={3}
                  gap={0}
                  // barColor="#1f6696"
                  // barPlayedColor="#a0c6ff"
                />
                <audio
                  src={URL.createObjectURL(el.audio as Blob)}
                  controlsList="nodownload"
                  controls
                />
                <span>{el.text ? el.text : "Не удалось распознать"}</span>
              </div>
            ) : (
              <span style={{ whiteSpace: "normal" }}>{el.text as string}</span>
            )}
            <span style={{ fontSize: "12px", alignSelf: "flex-end" }}>
              {el.date}
            </span>
          </MessageItem>
        ))}
      </ChatList>
    </ChatWrapper>
  );
};
