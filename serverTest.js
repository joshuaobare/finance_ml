const serverFn = async (features) => {
    try {
        const request = await fetch("http://localhost:8080", {
              method: "POST",
              headers: { "Content-type": "application/json" },
              body: JSON.stringify({ features })
            })
        const response = await request.json()
        console.log(response)
        
    } catch (error) {
        console.error(error)
    }
    }

serverFn([1])