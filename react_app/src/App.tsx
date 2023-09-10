import React, { useEffect, useState } from "react";
import "./App.css";
import styled from "styled-components";
import { Header } from "./Components/Header";
import { MessageInput } from "./Components/MessageInput";
import { ChatContainer } from "./Components/ChatContainer";
import { MessageType, SenderEnum, TypeEnum } from "./types/message";
import { getCurrentTime } from "./utils/currentTime";
import { Checkbox, ConfigProvider, Modal, Select, Space } from "antd";
import { trains } from "./const/trains";

const Container = styled.div`
  max-width: 600px;
  width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;

  @media (max-width: 768px) {
    width: 100%;
  }
`;

const MainBackground = styled.div`
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
  height: 100vh;

  @keyframes gradient {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }
`;

function App() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [train, setTrain] = useState<number>(1);
  const [isAiEnabled, setIsAiEnabled] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  console.log(isAiEnabled);
  const showModal = () => {
    setIsModalOpen(true);
  };

  const handleOk = () => {
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };

  useEffect(() => {
    const baseItem = {
      sender: SenderEnum.SERVER,
      type: TypeEnum.TEXT,
      text: "Вас приветствует помощник машиниста!",
      date: getCurrentTime(),
    };
    setIsModalOpen(true);
    setMessages([baseItem]);
  }, []);

  const setNewMessage = (message: MessageType) => {
    setMessages((prev) => [...prev, message]);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#e31b1a",
        },
      }}
    >
      <MainBackground>
        <Modal
          title="Выбор поезда"
          open={isModalOpen}
          onOk={handleOk}
          onCancel={handleCancel}
        >
          <Space direction="vertical" size="middle">
            <Select
              style={{ width: 220 }}
              showSearch
              defaultActiveFirstOption
              onChange={(value) => setTrain(+value + 1)}
              options={trains.map((el, index) => ({
                label: el,
                value: index.toString(),
              }))}
            />
            <Checkbox
              value={isAiEnabled}
              onChange={(e) => setIsAiEnabled(e.target.checked)}
            >
              Использовать AI - ассистент
            </Checkbox>
          </Space>
        </Modal>
        <Container>
          <Header showModal={showModal} />
          <ChatContainer messages={messages} />
          <MessageInput
            docId={+train}
            isAiEnabled={isAiEnabled}
            setNewMessage={setNewMessage}
          />
        </Container>
      </MainBackground>
    </ConfigProvider>
  );
}

export default App;
