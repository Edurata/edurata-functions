const handler = (inputs) => {
  const { code } = inputs;
  const func = new Function("inputs", code);
  const outputs = func(inputs.inputs);
  return { outputs };
};

console.log(
  handler({
    code: `
  const { arrays } = inputs;
  const array = arrays.reduce((acc, curr) => acc.concat(curr));
  return { array };
  `,
    inputs: {
      arrays: [
        [1, 2],
        [3, 4],
      ],
    },
  })
);
