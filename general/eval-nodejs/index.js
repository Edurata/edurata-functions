export const handler = async (inputs) => {
  const { code, input } = inputs;
  console.log("code", code);
  console.log("input", input);
  try {
    const func = new Function("input", code);
    const output = func(input);
    return { output };
  } catch (error) {
    return { error: error.toString(), stackTrace: error.stack };
  }
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

// console.log(
//   handler({
//     code: "const today = new Date(); return input.filter(record => { const releaseDate = new Date(record.fields.releaseDate); return today > releaseDate; });",
//     input: [
//       {
//         fields: {
//           releaseDate: "2021-01-01",
//         },
//       },
//     ],
//   })
// );
