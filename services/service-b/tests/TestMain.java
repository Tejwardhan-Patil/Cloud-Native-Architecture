import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.util.List;
import java.util.Arrays;
import java.util.Collections;

public class TestMain {

    private ServiceB serviceB;
    private DependencyService dependencyService;

    @BeforeEach
    public void setUp() {
        dependencyService = mock(DependencyService.class);
        serviceB = new ServiceB(dependencyService);
    }

    @Test
    public void testServiceBMainFunctionality_Success() {
        // Given
        String input = "testInput";
        String expectedOutput = "expectedOutput";

        // When
        when(dependencyService.process(input)).thenReturn(expectedOutput);
        String result = serviceB.processInput(input);

        // Then
        assertEquals(expectedOutput, result);
        verify(dependencyService, times(1)).process(input);
    }

    @Test
    public void testServiceBMainFunctionality_Failure() {
        // Given
        String input = "invalidInput";

        // When
        when(dependencyService.process(input)).thenThrow(new RuntimeException("Processing failed"));
        
        // Then
        assertThrows(RuntimeException.class, () -> serviceB.processInput(input));
        verify(dependencyService, times(1)).process(input);
    }

    @Test
    public void testNullInput() {
        // Given
        String input = null;

        // Then
        assertThrows(IllegalArgumentException.class, () -> serviceB.processInput(input));
    }

    @Test
    public void testEmptyInput() {
        // Given
        String input = "";

        // Then
        assertThrows(IllegalArgumentException.class, () -> serviceB.processInput(input));
    }

    @Test
    public void testWhitespaceInput() {
        // Given
        String input = "   ";

        // Then
        assertThrows(IllegalArgumentException.class, () -> serviceB.processInput(input));
    }

    @Test
    public void testSpecialCharacterInput() {
        // Given
        String input = "!@#$%^&*()";

        // When
        when(dependencyService.process(input)).thenReturn("processedSpecialCharacters");
        String result = serviceB.processInput(input);

        // Then
        assertEquals("processedSpecialCharacters", result);
        verify(dependencyService, times(1)).process(input);
    }

    @Test
    public void testLongStringInput() {
        // Given
        String input = String.join("", Collections.nCopies(1000, "a")); // 1000 'a's
        String expectedOutput = "longProcessed";

        // When
        when(dependencyService.process(input)).thenReturn(expectedOutput);
        String result = serviceB.processInput(input);

        // Then
        assertEquals(expectedOutput, result);
        verify(dependencyService, times(1)).process(input);
    }

    @Test
    public void testMultipleInputs_Success() {
        // Given
        List<String> inputs = Arrays.asList("input1", "input2", "input3");
        List<String> expectedOutputs = Arrays.asList("output1", "output2", "output3");

        // When
        when(dependencyService.process("input1")).thenReturn("output1");
        when(dependencyService.process("input2")).thenReturn("output2");
        when(dependencyService.process("input3")).thenReturn("output3");

        for (int i = 0; i < inputs.size(); i++) {
            String result = serviceB.processInput(inputs.get(i));
            assertEquals(expectedOutputs.get(i), result);
        }

        // Then
        verify(dependencyService, times(1)).process("input1");
        verify(dependencyService, times(1)).process("input2");
        verify(dependencyService, times(1)).process("input3");
    }

    @Test
    public void testMultipleInputs_Failure() {
        // Given
        List<String> inputs = Arrays.asList("validInput", "invalidInput", "validInput2");

        // When
        when(dependencyService.process("validInput")).thenReturn("validOutput");
        when(dependencyService.process("invalidInput")).thenThrow(new RuntimeException("Processing failed"));
        when(dependencyService.process("validInput2")).thenReturn("validOutput2");

        // Then
        assertEquals("validOutput", serviceB.processInput("validInput"));
        assertThrows(RuntimeException.class, () -> serviceB.processInput("invalidInput"));
        assertEquals("validOutput2", serviceB.processInput("validInput2"));

        verify(dependencyService, times(1)).process("validInput");
        verify(dependencyService, times(1)).process("invalidInput");
        verify(dependencyService, times(1)).process("validInput2");
    }

    @Test
    public void testProcessListOfInputs() {
        // Given
        List<String> inputs = Arrays.asList("input1", "input2", "input3");
        List<String> expectedOutputs = Arrays.asList("output1", "output2", "output3");

        // When
        when(dependencyService.process("input1")).thenReturn("output1");
        when(dependencyService.process("input2")).thenReturn("output2");
        when(dependencyService.process("input3")).thenReturn("output3");

        List<String> results = serviceB.processInputs(inputs);

        // Then
        assertEquals(expectedOutputs, results);
        verify(dependencyService, times(1)).process("input1");
        verify(dependencyService, times(1)).process("input2");
        verify(dependencyService, times(1)).process("input3");
    }

    @Test
    public void testProcessListWithFailure() {
        // Given
        List<String> inputs = Arrays.asList("input1", "input2", "input3");

        // When
        when(dependencyService.process("input1")).thenReturn("output1");
        when(dependencyService.process("input2")).thenThrow(new RuntimeException("Processing failed"));
        when(dependencyService.process("input3")).thenReturn("output3");

        // Then
        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            serviceB.processInputs(inputs);
        });
        assertEquals("Processing failed", exception.getMessage());
    }

    @Test
    public void testProcessNullList() {
        // Given
        List<String> inputs = null;

        // Then
        assertThrows(IllegalArgumentException.class, () -> serviceB.processInputs(inputs));
    }

    @Test
    public void testProcessEmptyList() {
        // Given
        List<String> inputs = Collections.emptyList();
        List<String> expectedOutputs = Collections.emptyList();

        // When
        List<String> results = serviceB.processInputs(inputs);

        // Then
        assertEquals(expectedOutputs, results);
        verify(dependencyService, times(0)).process(anyString());
    }

    @Test
    public void testProcessMixedInputList() {
        // Given
        List<String> inputs = Arrays.asList("valid1", "invalid", "valid2");

        // When
        when(dependencyService.process("valid1")).thenReturn("output1");
        when(dependencyService.process("invalid")).thenThrow(new RuntimeException("Processing failed"));
        when(dependencyService.process("valid2")).thenReturn("output2");

        // Then
        RuntimeException exception = assertThrows(RuntimeException.class, () -> {
            serviceB.processInputs(inputs);
        });
        assertEquals("Processing failed", exception.getMessage());
    }

    @Test
    public void testProcessLargeList() {
        // Given
        List<String> inputs = Collections.nCopies(1000, "input");
        String expectedOutput = "output";

        // When
        when(dependencyService.process(anyString())).thenReturn(expectedOutput);
        List<String> results = serviceB.processInputs(inputs);

        // Then
        assertEquals(Collections.nCopies(1000, expectedOutput), results);
        verify(dependencyService, times(1000)).process("input");
    }
}