const handler = (event) => {
  const { arrays } = event;
  const array = arrays.reduce((acc, curr) => acc.concat(curr));
  return { array };
};
