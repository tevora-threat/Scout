import axios from "axios";
const url = "https://10.6.6.13/api/polls/";

class PollService {
  static getPolls() {
    return new Promise(async (resolve, reject) => {
      try {
        const res = await axios.get(url);
        const data = res.data;

        resolve(
          data.map(poll => ({
            ...poll,
            createdAt: new Date(poll.createdAt)
          }))
        );
      } catch (err) {
        reject(err);
      }
    });
  }

  static getDrivePolls(driveID) {
    console.log('trying to get drive polls for', driveID);



    return new Promise(async (resolve, reject) => {
      try {
        const res = await axios.get(`${url}${driveID}`);
        const data = res.data;
        console.log(res);


        resolve(
          data.map(poll => ({
            ...poll,
            createdAt: new Date(poll.createdAt)
          }))
        );
      } catch (err) {
        reject(err);
        console.log(err);

      }
    });


  }

  static getMultipleDrivePolls(driveIDarray) {
    console.log('trying to get drive polls for', driveIDarray);
    var returnArray = []
    driveIDarray.forEach(driveID => {
      new Promise(async (resolve, reject) => {
        try {
          const res = await axios.get(`${url}${driveID}`);
          const data = res.data;
          console.log(data);

          returnArray.push(data)

          resolve(
            data.map(poll => ({
              ...poll,
              createdAt: new Date(poll.createdAt)
            }))
          );
        } catch (err) {
          reject(err);
          console.log(err);

        }
      });
    });
    console.log(`returnArray:${returnArray}`);

    return returnArray



  }


  static insertPoll(text) {
    return axios.poll(url, {
      text
    });
  }

  static deletePoll(id) {
    return axios.delete(`${url}${id}`);
  }
}

export default PollService;