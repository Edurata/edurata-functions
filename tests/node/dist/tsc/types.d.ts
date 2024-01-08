export type Inputs = {
    message: string;
    sleepTime: number | string;
    infile?: string;
};
export type Outputs = {
    sleepTime: number;
    outfile?: string;
    dummyfile?: string;
};
export type Handler = (inputs: Inputs) => Promise<Outputs>;
