//
//  ImageButton.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "ImageButton.h"

@interface ImageButton ()

- (BOOL)touchIsInView:(UITouch *)touch;

@end

@implementation ImageButton

- (void)setTarget:(id)aTarget action:(SEL)anAction
{
    target = aTarget;
    action = anAction;
}

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event
{
    self.highlighted = YES;
    isInside = YES;
}

- (void)touchesCancelled:(NSSet *)touches withEvent:(UIEvent *)event
{
    self.highlighted = NO;
    isInside = NO;
}

- (void)touchesMoved:(NSSet *)touches withEvent:(UIEvent *)event
{
    if (isInside && ![self touchIsInView:[touches anyObject]])
    {
        self.highlighted = NO;
        isInside = NO;
    }
    else if (!isInside && [self touchIsInView:[touches anyObject]])
    {
        self.highlighted = YES;
        isInside = YES;
    }
}

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event
{
    if ([self touchIsInView:[touches anyObject]])
    {
        self.highlighted = NO;
        [target performSelector:action withObject:self];
    }
}

#pragma mark -
#pragma mark Private methods

- (BOOL)touchIsInView:(UITouch *)touch
{
    CGPoint p = [touch locationInView:self];
    
    return ((p.x < self.bounds.size.width) && (p.y < self.bounds.size.height)
            && (p.x >= 0) && (p.y >= 0));
}

@end
