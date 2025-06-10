package com.alibaba.example.unitTest;

import com.taobao.pandora.boot.test.junit4.DelegateTo;
import com.taobao.pandora.boot.test.junit4.PandoraBootRunner;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.junit.MockitoJUnitRunner;

import java.util.Random;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.withSettings;

@RunWith(PandoraBootRunner.class)
@DelegateTo(MockitoJUnitRunner.class)
public class MockitoAnnotationNoSpringContextTest {

    @Test
    public void testRandom() {
        Random mockRandom = mock(Random.class, withSettings().withoutAnnotations());
        when(mockRandom.nextInt()).thenReturn(100);

        Assert.assertEquals(100, mockRandom.nextInt());
        Assert.assertEquals(100, mockRandom.nextInt());
    }
}
