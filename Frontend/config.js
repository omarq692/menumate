//Automatically switches between local and tunnel depending on domain
const API_BASE_URL = location.hostname.includes("localhost")
  ? "http://localhost:5000"
  : "https://menumate-dev.loca.lt";  //This needs to be change to your local tunneling link (testing).
