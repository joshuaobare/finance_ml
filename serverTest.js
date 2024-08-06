const serverFn = async () => {
  try {
    const request = await fetch("http://localhost:7000/predict", {
      method: "GET",
      headers: { "Content-type": "application/json" },
    });
    const response = await request.json();
    console.log(response);
  } catch (error) {
    console.error(error);
  }
};

serverFn([1]);
