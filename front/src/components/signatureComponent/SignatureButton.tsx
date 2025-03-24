import React, { useState, useRef } from "react";
import CanvasDraw from "react-canvas-draw";
import { GithubPicker, ColorResult } from "react-color";
import {
  Box,
  Button,
  Modal,
  Group,
  Popover,
  Text,
  Tooltip,
  Center,
  Paper,
  ActionIcon,
  Image,
  Tabs,
  ThemeIcon,
  useMantineColorScheme,
} from "@mantine/core";
import { Dropzone, MIME_TYPES } from "@mantine/dropzone";
import {
  IconPalette,
  IconArrowBackUp,
  IconTrash,
  IconCheck,
  IconSignature,
  IconUpload,
  IconPencil,
  IconPhoto,
} from "@tabler/icons-react";
import { COLORS, inkColors } from "../../colors";
import {
  CanvasDrawExtended,
  CanvasDrawProps,
  defaultProps,
  SignatureModalProps,
} from "../../types/signatureModalButton";

const width = `${Math.ceil(inkColors.length / 2) * 32}px`;

export default function SignatureButton({
  onSignatureSave,
}: SignatureModalProps) {
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [savedSignature, setSavedSignature] = useState<string>("");
  const canvasRef = useRef<CanvasDrawExtended>(null);
  const [brushColor, setBrushColor] = useState<string>(COLORS.black);
  const [showColor, setShowColor] = useState<boolean>(false);
  const [signatureData, setSignatureData] = useState<string>("");
  const [signatureStatus, setSignatureStatus] = useState<
    "empty" | "signed" | "confirmed"
  >("empty");
  const [activeTab, setActiveTab] = useState<string | null>("draw");
  const [canvasKey, setCanvasKey] = useState<number>(0);
  const { colorScheme } = useMantineColorScheme();

  const handleTabChange = (value: string | null) => {
    if (value) {
      setActiveTab(value);

      if (value === "draw") {
        setCanvasKey((prev) => prev + 1);
      }
      setSignatureStatus("empty");
      setSignatureData("");
    }
  };

  const getImg = (): string => {
    if (canvasRef.current && canvasRef.current.canvasContainer.children[1]) {
      return canvasRef.current.canvasContainer.children[1].toDataURL();
    }
    return "";
  };

  const handleClear = (): void => {
    if (canvasRef.current) {
      canvasRef.current.clear();
      setSignatureData("");
      setSignatureStatus("empty");
    }
  };

  const isCanvasEmpty = (): boolean => {
    if (canvasRef.current) {
      const linesData = canvasRef.current.getSaveData();
      try {
        const parsedData = JSON.parse(linesData);
        return !parsedData.lines || parsedData.lines.length === 0;
      } catch (e) {
        return true;
      }
    }
    return true;
  };

  const handleCanvasChange = (): void => {
    if (isCanvasEmpty()) {
      setSignatureData("");
      setSignatureStatus("empty");
      return;
    }

    const data = getImg();
    setSignatureData(data);
    if (data && data.length > 1000) {
      setSignatureStatus("signed");
    } else {
      setSignatureStatus("empty");
    }
  };

  const handleUndo = (): void => {
    if (canvasRef.current) {
      canvasRef.current.undo();

      if (isCanvasEmpty()) {
        setSignatureData("");
        setSignatureStatus("empty");
      } else {
        const data = getImg();
        setSignatureData(data);
        setSignatureStatus("signed");
      }
    }
  };

  const handleSignatureUpload = (files: File[]) => {
    if (files.length === 0) return;

    const file = files[0];
    const reader = new FileReader();

    reader.onload = (e) => {
      if (e.target && typeof e.target.result === "string") {
        setSignatureData(e.target.result);
        setSignatureStatus("signed");
      }
    };

    reader.readAsDataURL(file);
  };

  const saveSignature = (): void => {
    if (signatureStatus === "signed" && signatureData.length > 5000) {
      setSavedSignature(signatureData);
      onSignatureSave(signatureData);
      setModalOpen(false);
    }
  };

  const props: CanvasDrawProps = {
    ...defaultProps,
    className: "canvas",
    onChange: handleCanvasChange,
    brushColor,
    catenaryColor: brushColor,
  };

  const resetCanvas = () => {
    setSignatureStatus("empty");
    setSignatureData("");
    setActiveTab("draw");
    setCanvasKey((prev) => prev + 1);
  };

  return (
    <>
      <Box
        p="md"
        style={(theme) => ({
          borderRadius: theme.radius.md,
          border: `0.5px solid ${
            colorScheme == "light" ? COLORS.grayDark : COLORS.grayLight
          }`,
          maxWidth: "100%",
          width: "100%",
        })}
      >
        <Group justify="space-between" align="center">
          <Group>
            <ThemeIcon size="xl" radius="xl">
              <IconSignature size={24} />
            </ThemeIcon>

            <Box>
              <Text fw={600} size="lg">
                Digital Signature Required
              </Text>
              <Text c={COLORS.dimmed}>Sign to approve this agreement</Text>
            </Box>
          </Group>

          <Button
            variant="light"
            color={COLORS.blue}
            rightSection={<span>→</span>}
            radius="md"
            onClick={() => {
              setModalOpen(true);
              resetCanvas();
            }}
          >
            {savedSignature ? "Update Signature" : "Sign Now"}
          </Button>
        </Group>
      </Box>

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

      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Signature Capture"
        size="lg"
        centered
      >
        <Paper>
          <Text c={COLORS.dimmed} ta="center" size="sm" mb="md">
            Please add your signature
          </Text>

          <Tabs
            defaultValue="draw"
            value={activeTab}
            onChange={handleTabChange}
            mb="md"
          >
            <Tabs.List grow>
              <Tabs.Tab value="draw" leftSection={<IconPencil size={16} />}>
                Draw
              </Tabs.Tab>
              <Tabs.Tab value="upload" leftSection={<IconPhoto size={16} />}>
                Upload
              </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="draw" pt="md">
              <Box
                style={{
                  border: "1px dashed #ccc",
                  borderRadius: "4px",
                  padding: "10px",
                }}
              >
                <Center>
                  <CanvasDraw
                    key={canvasKey}
                    {...props}
                    ref={canvasRef as React.RefObject<CanvasDraw>}
                    lazyRadius={0}
                    hideGrid
                  />
                </Center>
              </Box>

              <Group align="center" my="md">
                <Popover
                  opened={showColor}
                  onChange={setShowColor}
                  position="bottom"
                  withArrow
                  shadow="md"
                >
                  <Popover.Target>
                    <Button
                      leftSection={<IconPalette size={18} />}
                      variant="light"
                      onClick={() => setShowColor((s) => !s)}
                      style={{
                        backgroundColor: brushColor,
                        color:
                          brushColor === COLORS.white
                            ? COLORS.black
                            : COLORS.white,
                      }}
                      size="sm"
                    >
                      Ink Color
                    </Button>
                  </Popover.Target>
                  <Popover.Dropdown>
                    <GithubPicker
                      triangle="hide"
                      color={brushColor}
                      colors={inkColors}
                      width={width}
                      onChangeComplete={(c: ColorResult) => {
                        setBrushColor(c.hex);
                        setShowColor(false);
                      }}
                    />
                  </Popover.Dropdown>
                </Popover>

                <Tooltip label="Undo">
                  <ActionIcon
                    variant="light"
                    color={COLORS.blue}
                    size="lg"
                    onClick={handleUndo}
                  >
                    <IconArrowBackUp size={20} />
                  </ActionIcon>
                </Tooltip>

                <Tooltip label="Clear Signature">
                  <ActionIcon
                    variant="light"
                    color={COLORS.red}
                    size="lg"
                    onClick={handleClear}
                  >
                    <IconTrash size={20} />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Tabs.Panel>

            <Tabs.Panel value="upload" pt="md">
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
            </Tabs.Panel>
          </Tabs>

          {signatureStatus === "signed" && (
            <Box mt="md" mb="md">
              <Text size="sm" fw={500} c="blue.8" mb="xs">
                Signature Preview:
              </Text>
              <Center>
                <Image
                  src={signatureData}
                  alt="Signature"
                  w="auto"
                  h={100}
                  fit="contain"
                  bg={COLORS.white}
                />
              </Center>
            </Box>
          )}

          <Group justify="flex-end" mt="lg">
            <Button variant="light" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              leftSection={<IconCheck size={18} />}
              onClick={saveSignature}
              disabled={signatureStatus !== "signed"}
              color="blue"
            >
              Save Signature
            </Button>
          </Group>
        </Paper>
      </Modal>
    </>
  );
}
