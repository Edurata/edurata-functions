type process = {
  env: {
    GOOGLE_SERVICE_ACCOUNT_EMAIL: string;
    GOOGLE_PRIVATE_KEY: string;
  };
};

export type Inputs = {
  spreadSheetId: string;
};

export type Outputs = {
  rows: object[];
};

export type Handler = (inputs: Inputs) => Promise<Outputs>;
