import { useState } from 'react';
import { Stepper, Button, Group, TextInput, Code } from '@mantine/core';
import { useForm } from '@mantine/form';

export function AgreementGenerator() {
  const [active, setActive] = useState(0);

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      ownerFullName: '',
      ownerEmailAddress: '',
      ownerAddress: '',
      tenantFullName: '',
      tenantEmailAddress: '',
      tenantAddress: '',
      website: '',
      github: '',
    },

    validate: (values) => {
      if (active === 0) {
        return {
          ownerFullName: values.ownerFullName.trim().length < 2 ? 'Name must include at least 2 characters' : null,
          ownerEmailAddress: /^\S+@\S+$/.test(values.ownerEmailAddress) ? null : 'Invalid email'
        };
      }

      if (active === 1) {
        return {
          tenantFullName: values.tenantFullName.trim().length < 2 ? 'Name must include at least 2 characters' : null,
          tenantEmailAddress: /^\S+@\S+$/.test(values.tenantEmailAddress) ? null : 'Invalid email',
        };
      }

      // if (active === 2) {
      //   return {
      //     tenantFullName: values.tenantFullName.trim().length < 2 ? 'Name must include at least 2 characters' : null,
      //     tenantEmailAddress: /^\S+@\S+$/.test(values.tenantEmailAddress) ? null : 'Invalid email',
      //   };
      // }

      return {};
    },
  });

  const nextStep = () =>
    setActive((current) => {
      if (form.validate().hasErrors) {
        return current;
      }
      return current < 4 ? current + 1 : current;
    });

  const prevStep = () => setActive((current) => (current > 0 ? current - 1 : current));

  return (
    <>
      <Stepper active={active}>
        <Stepper.Step label="First step" description="Owner Details">
          <TextInput
            label="Full name"
            placeholder="Type owner's full name here"
            key={form.key('ownerFullName')}
            {...form.getInputProps('ownerFullName')}
          />
          <TextInput
            mt="md"
            label="Email"
            placeholder="Type owner's email address here"
            key={form.key('ownerEmailAddress')}
            {...form.getInputProps('ownerEmailAddress')}
          />
          <TextInput
            mt="md"
            label="Address"
            placeholder="Type owner's address here"
            key={form.key('ownerAddress')}
            {...form.getInputProps('ownerAddress')}
          />
        </Stepper.Step>

        <Stepper.Step label="Second step" description="Tenant Details">
          <TextInput
            label="Full name"
            placeholder="Type tenant's full name here"
            key={form.key('tenantFullName')}
            {...form.getInputProps('tenantFullName')}
          />
          <TextInput
            mt="md"
            label="Email"
            placeholder="Type tenant's email address here"
            key={form.key('tenantEmailAddress')}
            {...form.getInputProps('tenantEmailAddress')}
          />
          <TextInput
            mt="md"
            label="Address"
            placeholder="Type tenant's address here"
            key={form.key('tenantAddress')}
            {...form.getInputProps('tenantAddress')}
          />
        </Stepper.Step>

        <Stepper.Step label="Third step" description="Agreement Details">
          <TextInput
            label="Website"
            placeholder="Website"
            key={form.key('website')}
            {...form.getInputProps('website')}
          />
          <TextInput
            mt="md"
            label="GitHub"
            placeholder="GitHub"
            key={form.key('github')}
            {...form.getInputProps('github')}
          />
        </Stepper.Step>

        <Stepper.Step label="Fourth step" description="Photo and documents upload">
          <TextInput
            label="Website"
            placeholder="Website"
            key={form.key('website')}
            {...form.getInputProps('website')}
          />
          <TextInput
            mt="md"
            label="GitHub"
            placeholder="GitHub"
            key={form.key('github')}
            {...form.getInputProps('github')}
          />
        </Stepper.Step>
        <Stepper.Completed>
          Completed! Form values:
          <Code block mt="xl">
            {JSON.stringify(form.getValues(), null, 2)}
          </Code>
        </Stepper.Completed>
      </Stepper>

      <Group justify="flex-end" mt="xl">
        {active !== 0 && (
          <Button variant="default" onClick={prevStep}>
            Back
          </Button>
        )}
        {active !== 4 && <Button onClick={nextStep}>Next step</Button>}
      </Group>
    </>
  );
}
