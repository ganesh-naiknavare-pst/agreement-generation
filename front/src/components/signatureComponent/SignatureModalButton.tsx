import React, { useState, useCallback } from "react";
import { Box, Text, Image, Button, Group } from "@mantine/core";
import { Dropzone, MIME_TYPES } from "@mantine/dropzone";
import { IconUpload, IconPencil, IconPhoto } from "@tabler/icons-react";
import { COLORS } from "../../colors";
import DrawSignatureModal from "./DrawSignatureModule";

interface SignatureComponentProps {
  onSignatureSave: (signatureData: string) => void;
}

export default function SignatureComponent({
  onSignatureSave,
}: SignatureComponentProps) {
  const [signatureData, setSignatureData] = useState("");
  const [savedSignature, setSavedSignature] = useState("");
  const [drawModalOpen, setDrawModalOpen] = useState(false);

  const signatureStatus = signatureData ? "signed" : "empty";

  const handleSave = useCallback(() => {
    if (signatureData) {
      setSavedSignature(signatureData);
      onSignatureSave(signatureData);
    }
  }, [signatureData, onSignatureSave]);

  const handleSignatureSave = useCallback(
    (drawnSignature: string) => {
      setSavedSignature(drawnSignature);
      onSignatureSave(drawnSignature);
    },
    [onSignatureSave]
  );

  const toggleDrawModal = useCallback(
    (isOpen: boolean) => () => {
      setDrawModalOpen(isOpen);
    },
    []
  );

  const handleSignatureUpload = useCallback((files: File[]) => {
    if (files.length === 0) return;

    const file = files[0];
    const reader = new FileReader();

    reader.onload = (e) => {
      if (e.target && typeof e.target.result === "string") {
        setSignatureData(e.target.result);
      }
    };

    reader.readAsDataURL(file);
  }, []);

  return (
    <>
      <Box>
        <Dropzone
          onDrop={handleSignatureUpload}
          accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
          p="xl"
        >
          <Group
            justify="center"
            align="center"
            style={{ pointerEvents: "none" }}
          >
            <IconUpload size={20} />
            <Text>Drag & drop or click to upload your signature.</Text>
          </Group>
        </Dropzone>
      </Box>

      {signatureStatus === "signed" && (
        <Box mt="md" mb="md">
          <Image
            src={signatureData}
            alt="Signature"
            w="auto"
            h={100}
            fit="contain"
          />
        </Box>
      )}

      <Group my={10}>
        <Button
          leftSection={<IconPhoto size={18} />}
          onClick={handleSave}
          variant="outline"
          color={COLORS.blue}
          disabled={!signatureData}
        >
          Click to Save Uploaded Signature
        </Button>
        <Text>OR</Text>
        <Button
          leftSection={<IconPencil size={18} />}
          onClick={toggleDrawModal(true)}
          variant="light"
          color={COLORS.blue}
        >
          Draw Signature
        </Button>
      </Group>

      <DrawSignatureModal
        opened={drawModalOpen}
        onClose={toggleDrawModal(false)}
        onSave={handleSignatureSave}
      />

      {savedSignature && (
        <Box mt="md">
          <Text size="sm" fw={500} c={COLORS.dimmed} mb="xs">
            Your signature:
          </Text>
          <Image
            src={savedSignature}
            alt="Signature"
            w="auto"
            h={100}
            fit="contain"
            bg={COLORS.white}
          />
        </Box>
      )}
    </>
  );
}
