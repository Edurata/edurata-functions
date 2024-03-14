declare const handler: (inputs: any) => Promise<{
    error: string;
    code?: undefined;
} | {
    code: any;
    error?: undefined;
}>;
export { handler };
