const handler = (inputs) => {
  const { code, input } = inputs;
  const func = new Function("input", code);
  let output;
  try {
    output = func(input);
  } catch (error) {
    output = error.message;
  }
  return { output };
};

// console.log(
//   handler({
//     code: `
//     const { arrays } = input;
//     const array = arrays.reduce((acc, curr) => acc.concat(curr));
//     return { array };
//     `,
//     input: {
//       arrays: [
//         [1, 2],
//         [3, 4],
//       ],
//     },
//   })
// );
