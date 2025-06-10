package com.alibaba.example.unitTest;

import com.alibaba.example.Application;
import com.taobao.pandora.boot.test.junit4.DelegateTo;
import com.taobao.pandora.boot.test.junit4.PandoraBootRunner;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import java.util.Random;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.withSettings;

@RunWith(PandoraBootRunner.class)
@DelegateTo(SpringRunner.class)
@SpringBootTest(classes = { Application.class })
public class MockitoAnnotationWithSpringContextTest {

    @Test
    public void testRandom() {
        Random mockRandom = mock(Random.class, withSettings().withoutAnnotations());
        when(mockRandom.nextInt()).thenReturn(100);

        Assert.assertEquals(100, mockRandom.nextInt());
        Assert.assertEquals(100, mockRandom.nextInt());
    }
}
