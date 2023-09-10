export type MessageType = {
  sender: SenderEnum;
  type: TypeEnum;
  text: string;
  audio?: Blob;
  date: string;
};

export enum TypeEnum {
  TEXT = "text",
  AUDIO = "audio",
}

export enum SenderEnum {
  SERVER = "server",
  USER = "user",
}
