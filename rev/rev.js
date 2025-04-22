const CryptoJS = require('crypto-js');
const { URLSearchParams } = require('url');
const dns = require('dns').promises;

// Configuration and state
const hostIP = "https://app.ecourts.gov.in/ecourt_mobile_DC/";
let jwttoken = "";
let regenerateWebserviceCallFlag = false;
let globaliv = "4B6250655368566D";
let globalIndex = 0;

// Show error message (replace alert with console)
function showErrorMessage(message) {
  console.error("Error:", message);
}

// Generate random hex
function genRanHex(size) {
  return [...Array(size)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
}

// Generate global IV
function generateGlobalIv() {
  const ivOptions = [
    "556A586E32723575", "34743777217A2543", "413F4428472B4B62",
    "48404D635166546A", "614E645267556B58", "655368566D597133"
  ];
  const indices = [0, 1, 2, 3, 4, 5];
  for (let i = indices.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  globaliv = ivOptions[indices[0]];
  globalIndex = indices[0];
  return globaliv;
}

// Encrypt data
function encryptData(data) {
  const dataEncoded = JSON.stringify(data);
  generateGlobalIv();
  const randomiv = genRanHex(16);
  const key = CryptoJS.enc.Hex.parse('4D6251655468576D5A7134743677397A');
  const iv = CryptoJS.enc.Hex.parse(globaliv + randomiv);

  const encrypted = CryptoJS.AES.encrypt(dataEncoded, key, { iv });
  let encrypted_data = encrypted.ciphertext.toString(CryptoJS.enc.Base64);
  encrypted_data = randomiv + globalIndex + encrypted_data;
  return encrypted_data;
}

// Decrypt response
function decodeResponse(result) {
  const key = CryptoJS.enc.Hex.parse('3273357638782F413F4428472B4B6250');
  const iv_random = CryptoJS.enc.Hex.parse(result.trim().slice(0, 32));
  const result_split = result.trim().slice(32);

  const bytes = CryptoJS.AES.decrypt(result_split, key, { iv: iv_random });
  let plaintext = bytes.toString(CryptoJS.enc.Utf8);
  plaintext = plaintext.replace(/[\u0000-\u0019]+/g, "");
  return plaintext;
}

// API call wrapper
async function callToWebService(url, data, callback) {
  try {
    const encryptedData = encryptData(data);
    const headers = {
      'Content-Type': 'application/json',
      'user-agent': 'eCourtsServices/2.0.1 (iPhone; iOS 18.4; Scale/3.00)'
    };

    headers['Authorization'] = 'Bearer ' + encryptData(jwttoken);

    // const params = new URLSearchParams({ action_code: encryptedData });
    // const fullUrl = `${url}?${params.toString()}`;
    const fullUrl = url;

    console.log(data);
    console.log(fullUrl);

    const res = await fetch(fullUrl, {
      method: 'GET',
      headers
    });

    const responseText = await res.text();

    console.log(`responseText:\n${responseText}\n`)
    const decodedResponse = JSON.parse(decodeResponse(responseText));

    if (decodedResponse.token) {
      jwttoken = decodedResponse.token;
    }

    console.log(decodedResponse)
    if (decodedResponse.status === 'N') {
      if (decodedResponse.status_code === '401') {
        if (!regenerateWebserviceCallFlag) {
          regenerateWebserviceCallFlag = true;
          const packageName = "com.eCourts.mobile";
          const uidObj = { uid: "324456:" + packageName };
          const newData = { ...data, ...uidObj };
          return await callToWebService(url, newData, callback);
        } else {
          showErrorMessage("Session expired!");
        }
      }

      if (decodedResponse.msg) {
        showErrorMessage(decodedResponse.msg);
      }

      return;
    }

    callback(decodedResponse);
    regenerateWebserviceCallFlag = false;

  } catch (error) {
    console.error('Error calling web service:', error.message);
    showErrorMessage("An error occurred while processing your request.");
    regenerateWebserviceCallFlag = false;
  }
}

// Fetch Court Complexes
async function getCourtComplexes(state_code, dist_code, callback) {
  const url = hostIP + "appReleaseWebService.php";
  let data = 'fillState';
  await callToWebService(url, data, callback);
}

getCourtComplexes("1", "101", (res) => {
  console.log("Court Complexes:", res.courtComplex);
});

console.log(decodeResponse('POaJ42M9nP6pkEJim6CFmQ=='));
