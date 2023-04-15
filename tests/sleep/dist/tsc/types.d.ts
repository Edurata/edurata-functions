export declare type Inputs = {
    sleepTimeMs: number;
    file?: string;
};
export declare type Outputs = {
    sleepTimeMs: number;
    file?: string;
};
export declare type Handler = (inputs: Inputs) => Promise<Outputs>;
