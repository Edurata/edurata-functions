const handler = (event) => {
  const { array, joinString } = event;
  return array.join(joinString);
};
