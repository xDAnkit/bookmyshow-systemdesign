import http from "k6/http";
import { sleep } from "k6";

export const options = {
  vus: 50,
  duration: "15s",
};

export default function () {
  const res = http.get("http://127.0.0.1:8080/api/v1/cities");

  // check response is 200
  if (res.status !== 200) {
    console.log("Fail: " + res.status);
  }
}
