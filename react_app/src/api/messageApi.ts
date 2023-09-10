import axios from "axios";
import { BASE_URL } from "../const/base";

export const sendAudioMessage = async (blob: Blob) => {
  let data = new File([blob], "123.webm");
  const formData = new FormData();
  formData.append("file", data);
  const res = await axios.post(`${BASE_URL}/speech_to_text`, formData);

  return res;
};

export const sendMessage = async (text: string, docId: number, ai: boolean) => {
  const res = await axios.post(`${BASE_URL}/send_message`, {
    message: text,
    document_id: docId || 10,
    ai: ai || false,
  });

  return res;
};
