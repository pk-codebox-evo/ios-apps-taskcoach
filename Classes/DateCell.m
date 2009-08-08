//
//  DateCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DateCell.h"


@implementation DateCell

@synthesize dateLabel;

- (void)dealloc
{
	[dateLabel release];
	
	[super dealloc];
}

- (void)setDate:(NSString *)date
{
	if (date)
	{
		dateLabel.text = date;
		[switch_ setOn:YES];
	}
	else
	{
		dateLabel.text = NSLocalizedString(@"None", @"No date set label");
		[switch_ setOn:NO];
	}
}

@end
