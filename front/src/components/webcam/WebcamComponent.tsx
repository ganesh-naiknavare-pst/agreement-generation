import React, { useState } from 'react'
import Webcam from 'react-webcam';
import { Dispatch, SetStateAction } from 'react';
import { Button } from "@mantine/core";
  

// Function to validate base64 image URI
const isValidBase64Image = (str) => {
    // Regex to check if string starts with a valid image MIME type
    const regex = /^data:image\/(png|jpeg|jpg|gif|webp|bmp|svg\+xml);base64,[A-Za-z0-9+/=]+$/;
    return regex.test(str);
};

interface WebcamComponentType {
  setShowCamera: Dispatch<SetStateAction<boolean>>
  setImageUrl: Dispatch<SetStateAction<string | null>>
  setImageUrlValid: Dispatch<SetStateAction<boolean>>
}

const videoConstraints = {
  facingMode: "user"
};

function WebcamComponent({ setShowCamera, setImageUrl, setImageUrlValid } : WebcamComponentType) {
  const webcamRef = React.useRef(null);

  const capture = React.useCallback(
    () => {
      const imageSrc = webcamRef.current.getScreenshot();
      setImageUrl(imageSrc)
      setShowCamera(false)

      if (isValidBase64Image(imageSrc)) {
        console.log(isValidBase64Image(imageSrc))
        console.log(imageSrc)
        setImageUrlValid(true)
      }
    },
    [webcamRef]
  );
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '2rem'
    }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '4px',
      }}>
      <Webcam
        audio={false}
        height={500}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={500}
        videoConstraints={videoConstraints}
      />
      <Button onClick={capture}>Capture photo</Button>
      </div>
    </div>
  )
}

export default WebcamComponent
