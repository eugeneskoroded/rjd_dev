import { SettingOutlined } from "@ant-design/icons";
import { Checkbox } from "antd";
import React, { FC } from "react";
import styled from "styled-components";
import logo from "../assets/img/logo.png";

const StyledHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  border-bottom: 1px solid #e31b1a;
  background: #ffff;
  padding: 0 8px;
`;

export const Header = ({ showModal }: any) => {
  return (
    <StyledHeader>
      <div
        style={{
          height: "100%",
          display: "flex",
          width: "80px",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <img style={{ height: "35px" }} src={logo} />
      </div>
      <h3 style={{ color: "#1f1f24" }}>Помощник машиниста</h3>
      <div
        style={{
          height: "100%",
          display: "flex",
          width: "80px",
          alignItems: "center",
          justifyContent: "flex-end",
        }}
      >
        <SettingOutlined onClick={showModal} />
      </div>
    </StyledHeader>
  );
};
