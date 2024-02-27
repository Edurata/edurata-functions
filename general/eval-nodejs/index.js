const handler = (inputs) => {
  const { code, input } = inputs;
  const func = new Function("input", code);
  const output = func(input);
  return { output };
};

console.log(
  handler({
    code: `
    const { arrays } = input;
    const array = arrays.reduce((acc, curr) => acc.concat(curr));
    return { array };
    `,
    input: {
      arrays: [
        [1, 2],
        [3, 4],
      ],
    },
  })
);
