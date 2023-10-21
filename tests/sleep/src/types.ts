export type Inputs = {
  sleepTime: number | string;
  file?: string;
};

export type Outputs = {
  sleepTime: number;
  file?: string;
};

export type Handler = (inputs: Inputs) => Promise<Outputs>;
