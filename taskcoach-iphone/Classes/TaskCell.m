//
//  TaskCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCell.h"
#import "CheckView.h"

#import "Task.h"
#import "TaskList.h"

@implementation TaskCell

@synthesize taskId;
@synthesize leftImage;
@synthesize titleLabel;

- (NSString *)trackingLedName
{
	return @"ledclock.png";
}

- (NSString *)completedLedName
{
	return @"ledgreen.png";
}

- (NSString *)overdueLedName
{
	return @"ledred.png";
}

- (NSString *)dueSoonLedName
{
	return @"ledorange.png";
}

- (NSString *)startedLedName
{
	return @"ledblue.png";
}

- (NSString *)notStartedLedName
{
	return @"ledgrey.png";
}

- (void)setTask:(Task *)task target:(id)theTarget action:(SEL)theAction
{
	taskId = task.objectId;
	target = theTarget;
	action = theAction;

	titleLabel.text = task.name;

	if ([task currentEffort])
	{
		leftImage.image = [UIImage imageNamed:[self trackingLedName]];
	}
	else
	{
		switch ([task taskStatus])
		{
			case TASKSTATUS_COMPLETED:
				leftImage.image = [UIImage imageNamed:[self completedLedName]];
				break;
			case TASKSTATUS_OVERDUE:
				leftImage.image = [UIImage imageNamed:[self overdueLedName]];
				break;
			case TASKSTATUS_DUESOON:
				leftImage.image = [UIImage imageNamed:[self dueSoonLedName]];
				break;
			case TASKSTATUS_STARTED:
				leftImage.image = [UIImage imageNamed:[self startedLedName]];
				break;
			case TASKSTATUS_NOTSTARTED:
				leftImage.image = [UIImage imageNamed:[self notStartedLedName]];
				break;
			default:
				break;
		}
	}

	[leftImage setTarget:self action:@selector(onTapImage)];

	if ([task childrenCount])
	{
		self.accessoryType = UITableViewCellAccessoryDetailDisclosureButton;
	}
	else
	{
		self.accessoryType = UITableViewCellAccessoryNone;
	}

	self.editingAccessoryType = UITableViewCellAccessoryDetailDisclosureButton;
}

- (void)dealloc
{
	[leftImage release];
	[titleLabel release];

	[super dealloc];
}

- (void)onTapImage
{
	isTapping = YES;
	[target performSelector:action withObject:self];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
	if (isTapping)
	{
		isTapping = NO;
		[super setSelected:NO animated:NO];
	}
	else
	{
		[super setSelected:selected animated:animated];
	}
}

@end
