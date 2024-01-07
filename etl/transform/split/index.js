const handler = (event) => {
  const { string, delimiter } = event;
  return string.split(delimiter);
};
